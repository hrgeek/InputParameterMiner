# InputParameterMiner
 Welcome to Input Parameter Miner!
    A tool to analyze websites for input fields, network requests,
    hidden parameters, and reflected values.

	Project Structure:
		InputParameterMiner/
		│
		├── __init__.py
		├── main.py
		├── setup.py
		├── install.sh
		├── requirements.txt
		│
		├── modules/
		│   ├── __init__.py
		│   ├── selenium_setup.py
		│   ├── input_extractor.py
		│   ├── network_analyzer.py
		│   ├── hidden_parameter_extractor.py
		│   ├── js_analyzer.py
		│   ├── reflected_value_tester.py
		│   ├── crawler.py
		│   ├── utils.py
		│
		└── results/
		    └── example.com.json  # Example output file
	     
How to Install:

	https://github.com/hrgeek/InputParameterMiner.git
	cd InputParameterMiner
	Make the install.sh Script Executable
 	chmod +x install.sh
  	./install.sh
   
Debugging Tips

	If you still encounter issues:
	Check the Installed Package
	pip3 show input_parameter_miner

Alternative: Use a Virtual Environment

	To avoid conflicts with system-wide Python packages, use a virtual environment:
	Create a Virtual Environment
	
		python3 -m venv venv
		source venv/bin/activate
	
	Install the Tool
		pip install .
How to Run:

	Basic Usage
		input-parameter-miner -u https://example.com
	 
	 Crawl with Custom Depth
		input-parameter-miner -u https://example.com -c -d 3
	    
	Save Results to a Directory
		input-parameter-miner -u https://example.com -o ./output
	     
	Uninstallation
		If you want to uninstall the tool, you can use pip:
		pip3 uninstall input_parameter_miner
	 
