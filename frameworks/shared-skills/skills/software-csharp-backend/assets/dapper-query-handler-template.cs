using System.Collections.Generic;
using System.Data;
using System.Threading;
using System.Threading.Tasks;
using Dapper;

namespace Company.Product.Reporting;

public sealed record FindCustomersQuery(string CountryCode, int PageSize, string? AfterCustomerCode);

public sealed record CustomerListItem(string CustomerCode, string DisplayName, string CountryCode);

public interface IFindCustomersQueryHandler
{
    Task<IReadOnlyList<CustomerListItem>> HandleAsync(FindCustomersQuery query, CancellationToken cancellationToken);
}

public sealed class FindCustomersQueryHandler : IFindCustomersQueryHandler
{
    private readonly IDbConnectionFactory _connectionFactory;

    public FindCustomersQueryHandler(IDbConnectionFactory connectionFactory)
    {
        _connectionFactory = connectionFactory;
    }

    public async Task<IReadOnlyList<CustomerListItem>> HandleAsync(FindCustomersQuery query, CancellationToken cancellationToken)
    {
        await using var connection = await _connectionFactory.OpenReadOnlyAsync(cancellationToken);

        const string sql =
            """
            select customer_code as CustomerCode,
                   display_name as DisplayName,
                   country_code as CountryCode
            from customers
            where country_code = @CountryCode
              and (@AfterCustomerCode is null or customer_code > @AfterCustomerCode)
            order by customer_code
            limit @PageSize;
            """;

        var command = new CommandDefinition(
            sql,
            new
            {
                query.CountryCode,
                query.PageSize,
                query.AfterCustomerCode,
            },
            cancellationToken: cancellationToken);

        var rows = await connection.QueryAsync<CustomerListItem>(command);
        return rows.AsList();
    }
}

public interface IDbConnectionFactory
{
    Task<IDbConnection> OpenReadOnlyAsync(CancellationToken cancellationToken);
}
