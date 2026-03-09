using System;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Windows;

namespace _260308_cs_input_window;

/// <summary>
/// Interaction logic for App.xaml
/// </summary>
public partial class App : Application
{
    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        var args = e.Args;
        int uIndex = Array.IndexOf(args, "-u");
        
        if (uIndex >= 0 && uIndex < args.Length - 1)
        {
            string accountName = args[uIndex + 1];
            
            Console.WriteLine($"Running in console mode for account: {accountName}");
            Console.Write("Enter password: ");
            
            // Note: In a real app we'd mask this, but for this exercise ReadLine is fine
            // string? password = Console.ReadLine();
            string password = ReadPassword();

            Console.WriteLine("\n--- Execution Details ---");
            Console.WriteLine($"Account Name: {accountName}");
            Console.WriteLine($"Password: {password}");
            Console.WriteLine($"All Arguments: {string.Join(" ", args)}");
            Console.WriteLine("-------------------------");

            // Exit the application, preventing the WPF window from opening
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
}
