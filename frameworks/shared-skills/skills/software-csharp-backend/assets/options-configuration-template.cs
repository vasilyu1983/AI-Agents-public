using System;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

namespace Company.Product.Configuration;

public sealed class PaymentsOptions
{
    public const string SectionName = "Payments";

    public string BaseUrl { get; init; } = string.Empty;

    public int TimeoutSeconds { get; init; } = 5;

    public int MaxRetries { get; init; } = 2;
}

public sealed class PaymentsOptionsValidator : IValidateOptions<PaymentsOptions>
{
    public ValidateOptionsResult Validate(string? name, PaymentsOptions options)
    {
        if (string.IsNullOrWhiteSpace(options.BaseUrl))
        {
            return ValidateOptionsResult.Fail("Payments:BaseUrl is required.");
        }

        if (!Uri.TryCreate(options.BaseUrl, UriKind.Absolute, out _))
        {
            return ValidateOptionsResult.Fail("Payments:BaseUrl must be an absolute URI.");
        }

        if (options.TimeoutSeconds <= 0 || options.TimeoutSeconds > 60)
        {
            return ValidateOptionsResult.Fail("Payments:TimeoutSeconds must be in range 1..60.");
        }

        if (options.MaxRetries < 0 || options.MaxRetries > 5)
        {
            return ValidateOptionsResult.Fail("Payments:MaxRetries must be in range 0..5.");
        }

        return ValidateOptionsResult.Success;
    }
}

public static class PaymentsOptionsRegistration
{
    public static IServiceCollection AddPaymentsOptions(this IServiceCollection services, IConfiguration configuration)
    {
        services
            .AddOptions<PaymentsOptions>()
            .Bind(configuration.GetSection(PaymentsOptions.SectionName))
            .ValidateOnStart();

        services.AddSingleton<IValidateOptions<PaymentsOptions>, PaymentsOptionsValidator>();

        return services;
    }
}
