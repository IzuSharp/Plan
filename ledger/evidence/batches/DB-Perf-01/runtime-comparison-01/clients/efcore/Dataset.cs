using System.Globalization;

internal static class Dataset
{
    internal static long CreatedAt(long id) => 1_700_000_000L + id / 4;
    internal static long? CustomerId(long id) => id % 7 == 0 ? null : id % 10 < 7 ? 1 + id % 8 : 9 + id % 248;
    internal static long Cents(long tenant, long id) => 100 + (tenant * 1009 + id * 37) % 100_000;
    internal static string? Note(long id) => id % 5 == 0 ? null : "note-" + (id % 16).ToString(CultureInfo.InvariantCulture);
    internal static string Channel(long id) => id % 2 == 0 ? "web" : "store";
    internal static bool Gift(long id) => id % 11 == 0;
    internal static string CustomerName(long id) => "Customer-" + id.ToString("D4", CultureInfo.InvariantCulture);
    internal static int Lines(long id) => id % 5 == 0 ? 0 : 1 + (int)(id % 3);
    internal static string Product(long id, int line) => "product-" + ((id * 7 + line) % 32).ToString("D2", CultureInfo.InvariantCulture);
    internal static long Quantity(long id, int line) => 1 + (id + line) % 7;

}
