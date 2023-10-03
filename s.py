from bs4 import BeautifulSoup
import re

def parse_endpoint(endpoint):
    if re.match(r'^https?://', endpoint):
        return {"host": endpoint}
    else:
        return {"host": re.sub(r'^https?://', '', endpoint)}

def convert_to_json(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

        findings = []
        for issue in soup.find_all('div', class_='Issues'):
            finding = {
                "title": issue.find('div', class_='Issue Type').text.strip(),
                "description": issue.find('div', class_='Threat Class').text.strip(),
                "severity": issue.find('div', class_='Severity').text.strip(),
                "mitigation": issue.find('div', class_='mitigation').text.strip(),
                "date": issue.find('div', class_='date').text.strip(),
                "cve": issue.find('div', class_='cve').text.strip(),
                "cwe": int(issue.find('div', class_='cwe').text.strip()),
                "cvssv3": issue.find('div', class_='cvssv3').text.strip(),
                "file_path": issue.find('div', class_='Path').text.strip(),
                "line": int(issue.find('div', class_='line').text.strip())
            }

            endpoints = issue.find('div', class_='endpoints')
            if endpoints:
                endpoints = [parse_endpoint(e.text.strip()) for e in endpoints.find_all('div', class_='endpoint')]
                finding["endpoints"] = endpoints

            findings.append(finding)

        return {"findings": findings}

# Example usage
html_path = "C:\\Users\\SYS\\Downloads\\d.html"
result = convert_to_json(html_path)
print(result)
