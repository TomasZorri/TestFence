# TestFence

TestFence is a website testing application designed to assess the security and code quality of a web application. It provides a versatile and user-friendly platform that enables comprehensive and automated testing.



## Main Features
* Comprehensive evaluation of website functionality to ensure proper operation.
* Generation of detailed reports with test results and recommendations. (Currently improving this functionality)


## Features
* Evaluation of code quality and detection of common errors in website functionality.
* Automated testing to identify potential gaps and vulnerabilities in website functionality.



## Installation and Usage

### Installation

```
git clone https://github.com/TomasZorri/TestFence.git
cd TestFence
pip install -r requirements.txt
python main.py
```


### Usage

1. Use the following functions for testing:

```python
# Set a new URL
set_url('URL', time_wait=True)

# Configure content
set_content('TAG', 'Attribute', 'contentAttribute', 'text', tag_navigation=True)

# Click on an element
click_element('TAG', 'Attribute', 'contentAttribute', time_wait=True, tag_navigation=True)

# Wait for the page to fully load
wait_page()
```

* The "time_wait=True" parameter in "click_element()" and "set_url()" functions is used to wait for the page to finish loading before performing the action. It functions similarly to the "wait_page()" function.
* The "tag_navigation=True" parameter indicates that the element will be searched first, centered on the screen, highlighted, and then the specified action will be performed. This parameter is only used in the "set_content()" and "click_element()" functions.


### Example Usage
1. Add the following code to this section:

![Code Section](img/info/section-code.jpg)


```python
# Set a new URL
set_url('https://www.google.com', time_wait=True)

# Configure content
set_content('textarea', 'class', 'gLFyf', 'que pasa si no dormimos')

# Click on the element
click_element('input', 'class', 'gNO89b', time_wait=True)

# Click on the element
click_element('a', 'href', 'https://businessinsider.mx/efectos-insomnio-que-pasa-si-dejas-de-dormir/', tag_navigation=True)

# Click on the element
wait_page()

# Set a new url
set_url('https://www.google.com')

# Click on the element
wait_page()
```

2. Once the code has been added in the same section, execute it by pressing "CTRL + B".



## Contributing

We welcome contributions! If you would like to contribute to TestFence, please follow these steps:

1. Fork the repository.

2. Create a new branch for your contribution:

```
git checkout -b your-branch-name
```
3. Make the necessary changes and improvements in your branch.

4. Commit your changes and push them to your forked repository:

```
git commit -m "Your commit message"
git push origin your-branch-name
```
5. Open a pull request in the original repository and provide a detailed description of your changes.

6. Our team will review your contribution and merge it if it meets the project's guidelines and standards.

7. Thank you for your contribution!



## License

TestFence is distributed under the Apache-2.0 License. For more details, please refer to the LICENSE file.
