using System.Text.Json.Serialization;

namespace NakhonPartsDashboard.Models;

public class TransactionModel
{
    [JsonPropertyName("date")]
    public string Date { get; set; } = "";

    [JsonPropertyName("sale_lot")]
    public string SaleLot { get; set; } = "";

    [JsonPropertyName("prod_id")]
    public string ProdId { get; set; } = "";

    [JsonPropertyName("amount")]
    public double Amount { get; set; }

    [JsonPropertyName("payment_type")]
    public List<string> PaymentType { get; set; } = new();

    public string PaymentTypeDisplay => string.Join(", ", PaymentType.Select(ThaiLabel));

    private static string ThaiLabel(string key) => key switch
    {
        "credit" => "เครดิต",
        "transfer" => "โอนเงิน",
        "cash" => "เงินสด",
        _ => key
    };
}

public class PaymentStat
{
    [JsonPropertyName("bill_count")]
    public int BillCount { get; set; }

    [JsonPropertyName("percent")]
    public double Percent { get; set; }

    [JsonPropertyName("total_amount")]
    public double TotalAmount { get; set; }
}

public class PaymentSummary
{
    [JsonPropertyName("credit")]
    public PaymentStat Credit { get; set; } = new();

    [JsonPropertyName("transfer")]
    public PaymentStat Transfer { get; set; } = new();

    [JsonPropertyName("cash")]
    public PaymentStat Cash { get; set; } = new();
}

public class TransactionsResponse
{
    [JsonPropertyName("transactions")]
    public List<TransactionModel> Transactions { get; set; } = new();

    [JsonPropertyName("payment_summary")]
    public PaymentSummary PaymentSummary { get; set; } = new();
}

public class DashboardResponse
{
    [JsonPropertyName("pos_cards")]
    public List<PosStatusModel> PosCards { get; set; } = new();

    [JsonPropertyName("transactions")]
    public List<TransactionModel> Transactions { get; set; } = new();

    [JsonPropertyName("payment_summary")]
    public PaymentSummary PaymentSummary { get; set; } = new();
}
