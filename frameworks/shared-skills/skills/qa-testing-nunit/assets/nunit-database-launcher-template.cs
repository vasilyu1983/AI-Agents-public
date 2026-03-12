using DotNet.Testcontainers.Builders;
using DotNet.Testcontainers.Networks;
using Microsoft.Data.SqlClient;
using Company.Product.Tests.Utils.Testcontainers.Migrator;
using Testcontainers.MsSql;

public sealed class DatabaseLaunchOptions
{
    public bool RunAuxiliaryMigrator { get; init; } = true;
}

public sealed class DatabaseLaunchResult
{
    public required MsSqlContainer Container { get; init; }
    public required string MainConnectionString { get; init; }
    public required string AuxiliaryConnectionString { get; init; }
    public required IReadOnlyCollection<string> MigratorExecutionOrder { get; init; }
}

public sealed class DatabaseLauncher : IAsyncDisposable
{
    private const string SqlServerAlias = "sql-db";
    private const string MainDatabaseName = "service_main";
    private const string AuxiliaryDatabaseName = "service_aux";

    private const string MainMigratorImage = "reg.corp.swiftcom.uk/sc.tool/sc_tool_fluentmigrator:latest";
    private const string DependencyMigratorImage = "reg.corp.swiftcom.uk/company/dependency-migrator:latest";
    private const string AuxiliaryMigratorImage = "reg.corp.swiftcom.uk/company/aux-migrator:latest";

    private readonly INetwork _network = new NetworkBuilder()
        .WithName("api_tests_network_" + Guid.NewGuid().ToString("N"))
        .WithDriver(NetworkDriver.Bridge)
        .WithCleanUp(true)
        .Build();

    private readonly List<MigratorContainer> _externalMigrators = [];
    private readonly List<string> _executionOrder = [];

    private MsSqlContainer? _sqlContainer;
    private MigratorContainer? _mainMigrator;

    public async Task<DatabaseLaunchResult> LaunchAsync(
        DatabaseLaunchOptions? options = null,
        CancellationToken cancellationToken = default)
    {
        options ??= new DatabaseLaunchOptions();

        await _network.CreateAsync(cancellationToken);

        _sqlContainer = MsSqlContainers.Create(_network, SqlServerAlias);
        await _sqlContainer.StartAsync(cancellationToken);

        await EnsureDatabaseExistsAsync(_sqlContainer.GetConnectionString(), MainDatabaseName, cancellationToken);
        await EnsureDatabaseExistsAsync(_sqlContainer.GetConnectionString(), AuxiliaryDatabaseName, cancellationToken);

        var mainConnectionString = BuildConnectionString(_sqlContainer.GetConnectionString(), MainDatabaseName, SqlServerAlias);
        var auxiliaryConnectionString = BuildConnectionString(_sqlContainer.GetConnectionString(), AuxiliaryDatabaseName, SqlServerAlias);

        await RunExternalMigratorAsync("dependency", DependencyMigratorImage, mainConnectionString, cancellationToken);
        await VerifyTableExistsAsync(mainConnectionString, "dbo", "RequiredDependencyTable", cancellationToken);

        if (options.RunAuxiliaryMigrator)
        {
            await RunExternalMigratorAsync("auxiliary", AuxiliaryMigratorImage, auxiliaryConnectionString, cancellationToken);
            await VerifyTableExistsAsync(auxiliaryConnectionString, "dbo", "AuxiliaryState", cancellationToken);
        }

        await RunMainMigratorAsync(mainConnectionString, ResolveMigrationsFolder(), cancellationToken);

        return new DatabaseLaunchResult
        {
            Container = _sqlContainer,
            MainConnectionString = mainConnectionString,
            AuxiliaryConnectionString = auxiliaryConnectionString,
            MigratorExecutionOrder = _executionOrder.ToArray()
        };
    }

    public async ValueTask DisposeAsync()
    {
        if (_mainMigrator is not null)
        {
            await _mainMigrator.DisposeAsync();
        }

        foreach (var migrator in _externalMigrators)
        {
            await migrator.DisposeAsync();
        }

        if (_sqlContainer is not null)
        {
            await _sqlContainer.DisposeAsync();
        }

        await _network.DisposeAsync();
        GC.SuppressFinalize(this);
    }

    private async Task RunExternalMigratorAsync(string name, string image, string connectionString, CancellationToken cancellationToken)
    {
        var migrator = MigratorContainers.CreateExternalMigrator(name, image, _network, connectionString);
        _externalMigrators.Add(migrator);
        await migrator.StartAsync(cancellationToken);
        _executionOrder.Add(name);
    }

    private async Task RunMainMigratorAsync(string connectionString, string migrationsFolder, CancellationToken cancellationToken)
    {
        _mainMigrator = MigratorContainers.CreateMainMigrator(MainMigratorImage, _network, connectionString, migrationsFolder);
        await _mainMigrator.StartAsync(cancellationToken);
        _executionOrder.Add("main");
    }

    private static string ResolveMigrationsFolder()
    {
        return Path.GetFullPath("../../../../../../db/migrations");
    }

    private static string BuildConnectionString(string sourceConnectionString, string databaseName, string sqlServerAlias)
    {
        var builder = new SqlConnectionStringBuilder(sourceConnectionString)
        {
            InitialCatalog = databaseName,
            DataSource = sqlServerAlias,
            Encrypt = false,
            TrustServerCertificate = true
        };

        return builder.ConnectionString;
    }

    private static async Task EnsureDatabaseExistsAsync(string sourceConnectionString, string databaseName, CancellationToken cancellationToken)
    {
        var builder = new SqlConnectionStringBuilder(sourceConnectionString)
        {
            InitialCatalog = "master",
            Encrypt = false,
            TrustServerCertificate = true
        };

        await using var connection = new SqlConnection(builder.ConnectionString);
        await connection.OpenAsync(cancellationToken);

        const string sql = "IF DB_ID(@dbName) IS NULL EXEC('CREATE DATABASE [' + @dbName + ']')";
        await using var command = new SqlCommand(sql, connection);
        command.Parameters.AddWithValue("@dbName", databaseName);
        await command.ExecuteNonQueryAsync(cancellationToken);
    }

    private static async Task VerifyTableExistsAsync(string connectionString, string schema, string table, CancellationToken cancellationToken)
    {
        const string sql = "SELECT COUNT(1) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=@schema AND TABLE_NAME=@table";

        await using var connection = new SqlConnection(connectionString);
        await connection.OpenAsync(cancellationToken);

        await using var command = new SqlCommand(sql, connection);
        command.Parameters.AddWithValue("@schema", schema);
        command.Parameters.AddWithValue("@table", table);

        var exists = Convert.ToInt32(await command.ExecuteScalarAsync(cancellationToken)) > 0;
        if (!exists)
        {
            throw new InvalidOperationException($"Expected table '{schema}.{table}' is missing after migrator execution.");
        }
    }
}

public static class MigratorContainers
{
    private static readonly string[] ExternalMigratorCommand = ["migrateup", "-m", "../sql"];

    public static MigratorContainer CreateExternalMigrator(string name, string image, INetwork network, string connectionString)
    {
        return new MigratorContainerBuilder()
            .WithImage(image)
            .WithName($"{name}_{Guid.NewGuid():N}")
            .WithNetwork(network)
            .WithDatabaseType(DatabaseType.SqlServer)
            .WithConnectionString(connectionString)
            .WithDatabaseSchema("dbo")
            .WithCommand(ExternalMigratorCommand)
            .Build();
    }

    public static MigratorContainer CreateMainMigrator(string image, INetwork network, string connectionString, string migrationsFolder)
    {
        return new MigratorContainerBuilder()
            .WithImage(image)
            .WithName("main_migrator_" + Guid.NewGuid().ToString("N"))
            .WithNetwork(network)
            .WithDatabaseType(DatabaseType.SqlServer)
            .WithConnectionString(connectionString)
            .WithDatabaseSchema("dbo")
            .WithMigrationsFolder(migrationsFolder)
            .WithDefaultMigratorCommand()
            .Build();
    }
}
