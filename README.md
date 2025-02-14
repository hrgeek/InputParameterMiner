# InputParameterMiner
 Welcome to Input Parameter Miner!
    A tool to analyze websites for input fields, network requests,
    hidden parameters, and reflected values.

	Project Structure:
		input_parameter_miner/
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
	 
