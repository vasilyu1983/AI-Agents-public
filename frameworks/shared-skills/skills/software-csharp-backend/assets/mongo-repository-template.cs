using System;
using System.Threading;
using System.Threading.Tasks;
using MongoDB.Bson.Serialization.Attributes;
using MongoDB.Driver;

namespace Company.Product.Persistence;

public interface IInvoiceRepository
{
    Task<InvoiceDocument?> FindByIdAsync(Guid invoiceId, CancellationToken cancellationToken);

    Task<bool> TryInsertAsync(InvoiceDocument document, CancellationToken cancellationToken);
}

public sealed class InvoiceRepository : IInvoiceRepository
{
    private readonly IMongoCollection<InvoiceDocument> _collection;

    public InvoiceRepository(IMongoDatabase database)
    {
        _collection = database.GetCollection<InvoiceDocument>("invoices");
    }

    public async Task<InvoiceDocument?> FindByIdAsync(Guid invoiceId, CancellationToken cancellationToken)
    {
        var filter = Builders<InvoiceDocument>.Filter.Eq(x => x.InvoiceId, invoiceId);
        return await _collection.Find(filter).FirstOrDefaultAsync(cancellationToken);
    }

    public async Task<bool> TryInsertAsync(InvoiceDocument document, CancellationToken cancellationToken)
    {
        try
        {
            await _collection.InsertOneAsync(document, cancellationToken: cancellationToken);
            return true;
        }
        catch (MongoWriteException ex) when (ex.WriteError?.Category == ServerErrorCategory.DuplicateKey)
        {
            return false;
        }
    }

    public static async Task EnsureIndexesAsync(IMongoCollection<InvoiceDocument> collection, CancellationToken cancellationToken)
    {
        var byInvoiceId = new CreateIndexModel<InvoiceDocument>(
            Builders<InvoiceDocument>.IndexKeys.Ascending(x => x.InvoiceId),
            new CreateIndexOptions { Unique = true, Name = "ux_invoice_id" });

        var byCustomerUpdated = new CreateIndexModel<InvoiceDocument>(
            Builders<InvoiceDocument>.IndexKeys
                .Ascending(x => x.CustomerId)
                .Descending(x => x.UpdatedAt),
            new CreateIndexOptions { Name = "ix_customer_updated" });

        await collection.Indexes.CreateManyAsync(new[] { byInvoiceId, byCustomerUpdated }, cancellationToken);
    }
}

public sealed class InvoiceDocument
{
    [BsonId]
    public Guid InvoiceId { get; init; }

    public Guid CustomerId { get; init; }

    public decimal Amount { get; init; }

    public DateTimeOffset UpdatedAt { get; init; }
}
