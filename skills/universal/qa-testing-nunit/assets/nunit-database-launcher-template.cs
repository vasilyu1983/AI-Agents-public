using DotNet.Testcontainers.Builders;
using DotNet.Testcontainers.Configurations;
using DotNet.Testcontainers.Containers;
using DotNet.Testcontainers.Networks;
using Microsoft.Data.SqlClient;
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

    // Pin every image to an explicit tag or digest; never ":latest" (Testcontainers best practice #8).
    private const string MainMigratorImage = "registry.example.com/company/main-migrator:<pinned-tag>";
    private const string DependencyMigratorImage = "registry.example.com/company/dependency-migrator:<pinned-tag>";
    private const string AuxiliaryMigratorImage = "registry.example.com/company/aux-migrator:<pinned-tag>";

    private readonly INetwork _network = new NetworkBuilder()
        .WithName("api_tests_network_" + Guid.NewGuid().ToString("N"))
        .WithDriver(NetworkDriver.Bridge)
        .WithCleanUp(true)
        .Build();

    private readonly List<IContainer> _externalMigrators = [];
    private readonly List<string> _executionOrder = [];

    private MsSqlContainer? _sqlContainer;
    private IContainer? _mainMigrator;

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
        await MigratorContainers.RunToSuccessAsync(migrator, name, cancellationToken);
        _executionOrder.Add(name);
    }

    private async Task RunMainMigratorAsync(string connectionString, string migrationsFolder, CancellationToken cancellationToken)
    {
        _mainMigrator = MigratorContainers.CreateMainMigrator(MainMigratorImage, _network, connectionString, migrationsFolder);
        await MigratorContainers.RunToSuccessAsync(_mainMigrator, "main", cancellationToken);
        _executionOrder.Add("main");
    }

    // Resolve from the repository root, not from the runner's working directory
    // (bin/<Configuration>/<TFM> depth changes between local, CI, and MTP runs).
    private static string ResolveMigrationsFolder()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git")))
        {
            directory = directory.Parent;
        }

        if (directory is null)
        {
            throw new InvalidOperationException("Repository root (.git) not found above " + AppContext.BaseDirectory);
        }

        var folder = Path.Combine(directory.FullName, "db", "migrations");
        return Directory.Exists(folder)
            ? folder
            : throw new DirectoryNotFoundException("Migrations folder not found: " + folder);
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

        // QUOTENAME keeps the dynamic DDL injection-safe even in test code.
        const string sql = "IF DB_ID(@dbName) IS NULL BEGIN DECLARE @ddl nvarchar(300) = N'CREATE DATABASE ' + QUOTENAME(@dbName); EXEC (@ddl); END";
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

public static class MsSqlContainers
{
    // Example pinned tag: look up the current CU tag on mcr.microsoft.com and bump deliberately.
    private const string Image = "mcr.microsoft.com/mssql/server:2022-CU27-ubuntu-22.04";

    public static MsSqlContainer Create(INetwork network, string alias)
    {
        return new MsSqlBuilder(Image)
            .WithNetwork(network)
            .WithNetworkAliases(alias)
            .Build();
    }
}

// One-shot migration containers built with plain Testcontainers APIs.
// Replace the three placeholders with what your migration image documents.
public static class MigratorContainers
{
    private const string ConnectionStringVariable = "<env var your migration image reads>";
    private const string CompletedLogMessage = "<line your migration tool logs on success>";
    private const string MigrationsPathInContainer = "/migrations/";
    private static readonly string[] MigrationCommand = ["<command your migration image documents>"];

    public static IContainer CreateExternalMigrator(string name, string image, INetwork network, string connectionString)
    {
        return CreateBuilder(image, $"{name}_{Guid.NewGuid():N}", network, connectionString).Build();
    }

    public static IContainer CreateMainMigrator(string image, INetwork network, string connectionString, string migrationsFolder)
    {
        // Copy the scripts in before start; host bind mounts break on remote Docker hosts (best practice #5).
        return CreateBuilder(image, "main_migrator_" + Guid.NewGuid().ToString("N"), network, connectionString)
            .WithResourceMapping(new DirectoryInfo(migrationsFolder), MigrationsPathInContainer)
            .Build();
    }

    // A migration job exits when it is done: fail setup unless the exit code is 0.
    public static async Task RunToSuccessAsync(IContainer migrator, string name, CancellationToken cancellationToken)
    {
        await migrator.StartAsync(cancellationToken);
        var exitCode = await migrator.GetExitCodeAsync(cancellationToken);
        if (exitCode != 0)
        {
            var (stdout, stderr) = await migrator.GetLogsAsync(ct: cancellationToken);
            throw new InvalidOperationException($"Migrator '{name}' exited with code {exitCode}.\n{stdout}\n{stderr}");
        }
    }

    private static ContainerBuilder CreateBuilder(string image, string containerName, INetwork network, string connectionString)
    {
        return new ContainerBuilder()
            .WithImage(image)
            .WithName(containerName)
            .WithNetwork(network)
            .WithEnvironment(ConnectionStringVariable, connectionString)
            .WithCommand(MigrationCommand)
            // OneShot mode treats a normal exit as success instead of a failed start.
            .WithWaitStrategy(Wait.ForUnixContainer()
                .UntilMessageIsLogged(CompletedLogMessage, o => o.WithMode(WaitStrategyMode.OneShot)));
    }
}
