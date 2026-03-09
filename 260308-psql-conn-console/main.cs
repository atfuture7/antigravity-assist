using System;
using System.IO;
using System.Data;
using System.Globalization;
using Npgsql;
using CsvHelper;

class Program
{
    static void Main(string[] args)
    {
        // 1. Connection Details
        string connString = "Host=localhost;Username=postgres;Password=your_password;Database=your_db_name";
        string sqlFilePath = "query.sql";
        string csvOutputPath = "results.csv";

        try
        {
            // 2. Open Connection
            using (var conn = new NpgsqlConnection(connString))
            {
                conn.Open();
                Console.WriteLine("Connected to PostgreSQL!");

                // 3. Read SQL file content
                string sqlQuery = File.ReadAllText(sqlFilePath);

                using (var cmd = new NpgsqlCommand(sqlQuery, conn))
                using (var reader = cmd.ExecuteReader())
                {
                    // 4. Write to CSV using CsvHelper
                    using (var writer = new StreamWriter(csvOutputPath))
                    using (var csv = new CsvWriter(writer, CultureInfo.InvariantCulture))
                    {
                        // Write the Header Row
                        for (int i = 0; i < reader.FieldCount; i++)
                        {
                            csv.WriteField(reader.GetName(i));
                        }
                        csv.NextRecord();

                        // Write the Data Rows
                        while (reader.Read())
                        {
                            for (int i = 0; i < reader.FieldCount; i++)
                            {
                                csv.WriteField(reader[i]);
                            }
                            csv.NextRecord();
                        }
                    }
                }
                Console.WriteLine($"Export complete: {csvOutputPath}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}