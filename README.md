# sonar-checkstyle-api-profile-importer
Import checkstyle xml configuration files into Sonarqube profile via Sonarqube Web API.

## Description
This script is supposed to work as a workaround for issue [checkstyle/sonar-checkstyle#2](https://github.com/checkstyle/sonar-checkstyle/issues/2). Since there is no way to define custom rule from a template rule when importing a profile as of now, it will mitigate the pain of manually registering checkstyle rules.

It communicates with Sonarqube server via web API for 2 times for every rule, so it could take some time to finish importing profile. It first **define custom rules** for each template rule. Then, it **creates a new profile** that will contain your check rules. Once the profile is created, it **activates** newly defined custom rules and non-template rules for the profile.

I tested on my computer(macOS Big Sur Version 11.2.3, Python 3.6.8) using the example xml file and it worked properly. If there is any issue, please feel free to create an issue.

## Usage
To import checkstyle configuration xml file into Sonarqube profile, execute the following command.
```bash
python3 importer.py --xml_path XML_PATH --profile_name PROFILE_NAME
                   --username USERNAME --password PASSWORD
                   [--server_url SERVER_URL]
```

To get further usage information, execute the following command.
```bash
python3 importer.py -h
```

## Feedbacks / Contributions / Issue Reporting
Every feedback or contribution is welcome! Please feel free to create a comment, feedback, issue or pull request.
