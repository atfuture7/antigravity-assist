using System;
using System.Globalization;

class Program
{
    static void Main(string[] args)
    {
        // Check for command line argument (the .sql file)
        string[] cmdArgs = Environment.GetCommandLineArgs();

        RunCliMode(cmdArgs); 
    }

    private static void RunCliMode(string[] args)
    {
        Console.WriteLine("Args: " + string.Join(", ", args.Skip(2)));
        //Console.WriteLine($"Processing file: {filePath}");
        Console.Write("Test showing input: "); string host = Console.ReadLine() ?? string.Empty;
        Console.Write("test hidden input: "); string pass = ReadPassword(); // Masked input

        //string connStr = $"Host={host};Port={port};Username={user};Password={pass};Database=postgres";
        Console.WriteLine($"\nverify info: view:{host}, hidden:{pass} ");
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
}