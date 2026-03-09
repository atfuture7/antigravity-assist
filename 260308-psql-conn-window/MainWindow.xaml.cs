using System;
using System.IO;
using System.Windows;
using Microsoft.Win32;
using Npgsql;
using System.Globalization;
using CsvHelper;


namespace _260308_psql_conn_cs;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }

    // --- GUI MODE: If no file was provided at startup ---
    private void Submit_Click(object sender, RoutedEventArgs e)
    {
        if (string.IsNullOrEmpty(TxtFile.Text)) { MessageBox.Show("Please select a file."); return; }

        string connStr = $"Host={TxtIp.Text};Port={TxtPort.Text};Username={TxtUser.Text};Password={TxtPass.Password};Database=postgres";
        ExecuteSqlExport(TxtFile.Text, connStr);
    }

    private void ExecuteSqlExport(string sqlPath, string connString)
    {
        try {
            using var conn = new NpgsqlConnection(connString);
            conn.Open();
            
            string sql = File.ReadAllText(sqlPath);
            using var cmd = new NpgsqlCommand(sql, conn);
            using var reader = cmd.ExecuteReader();

            string csvPath = Path.ChangeExtension(sqlPath, ".csv");
            using var writer = new StreamWriter(csvPath);
            using var csv = new CsvWriter(writer, CultureInfo.InvariantCulture);

            for (int i = 0; i < reader.FieldCount; i++) csv.WriteField(reader.GetName(i));
            csv.NextRecord();

            while (reader.Read()) {
                for (int i = 0; i < reader.FieldCount; i++) csv.WriteField(reader[i]);
                csv.NextRecord();
            }
            MessageBox.Show($"Done! Saved to {csvPath}");
        }
        catch (Exception ex) { MessageBox.Show("Error: " + ex.Message); }
    }

    private void Browse_Click(object sender, RoutedEventArgs e)
    {
        OpenFileDialog op = new OpenFileDialog { Filter = "SQL files (*.sql)|*.sql" };
        if (op.ShowDialog() == true) TxtFile.Text = op.FileName;
    }
}