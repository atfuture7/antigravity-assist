using System.Configuration;
using System.Data;
using System.Windows;
using System.Globalization;
using System.IO;

using Npgsql;
using CsvHelper;


namespace _260308_psql_conn_cs;

/// <summary>
/// Interaction logic for App.xaml
/// </summary>
public partial class App : Application
{

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        var args = e.Args;
        int uIndex = Array.IndexOf(args, "-i");
        Console.WriteLine($"All Arguments: {string.Join(" ", args)}");

        if (uIndex >= 0 && File.Exists(args[uIndex + 1]) && uIndex < args.Length - 1)
        {
            string sql_content = File.ReadAllText(args[uIndex + 1]);

            Console.WriteLine($"Running in console mode with sql file: {args[uIndex + 1]}");
        
            Console.Write("Enter Account: "); string accountName = Console.ReadLine() ?? string.Empty;
            Console.Write("Enter password: ");
            
            // Note: In a real app we'd mask this, but for this exercise ReadLine is fine
            // string? password = Console.ReadLine();
            string password = ReadPassword();

            Console.WriteLine("\n--- Execution Details ---");
            Console.WriteLine($"Account Name: {accountName}");
            Console.WriteLine($"Password: {password}");
            Console.WriteLine($"SQL Content: {sql_content}");
            Console.WriteLine("-------------------------");

            // Exit the application, preventing the WPF window from opening
            exec_sql(args[uIndex + 1], accountName, password);
            Environment.Exit(0);
        }
    }

    private static string ReadPassword()
    {
        string pass = "";
        do
        {
            ConsoleKeyInfo key = Console.ReadKey(true);
            if (key.Key != ConsoleKey.Backspace && key.Key != ConsoleKey.Enter)
            {
                pass += key.KeyChar;
                Console.Write("*");
            }
            else
            {
                if (key.Key == ConsoleKey.Backspace && pass.Length > 0)
                {
                    pass = pass.Substring(0, (pass.Length - 1));
                    Console.Write("\b \b");
                }
                else if (key.Key == ConsoleKey.Enter)
                {
                    break;
                }
            }
        } while (true);
        return pass;
    }
    
    private void exec_sql(string filePath, string accountName, string password)
    {
        string connString = $"Host=localhost;Username={accountName};Password={password};Database=your_db_name";
        string sqlFilePath = filePath;
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
        }        // This method can be used for additional startup logic if needed
    }

}

