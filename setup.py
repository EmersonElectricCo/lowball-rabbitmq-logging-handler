from setuptools import setup, find_packages

DESCRIPTION = "lowball-rabbitmq-logging-handler is a simple lowball module to log to a rabbitmq service"
VERSION = "1.0.0"


def read_requirements():
    """
    Simple helper method to read in the requirements.txt file and parse it into a list for consumption by setuptools
    :return: list of requirements
    """
    required = []
    with open("requirements.txt") as f:
        for line in f:
            if line[0] != "#":
                # Not a comment add it as a requirement
                required.append(line.split("#"))
    return required


def readme():
    """
    Helper to try and format the .md readme file for pretty printing. Falls back to short description.
    :return: The available description
    """
    try:
        import pypandoc
        description = pypandoc.convert_file('README.md', 'rst')
    except:
        description = DESCRIPTION

    return description


setup(name="lowball-rabbitmq-logging-handler",
      version=VERSION,
      description=DESCRIPTION,
      long_description=readme(),
      url="https://github.com/EmersonElectricCo/lowball-rabbitmq-logging-handler",
      author="Isaiah Eichen",
      author_email="ieichen137@gmail.com",
      license="Apache License 2.0",
      packages=[
          "lowball_rabbitmq_logging_handler"
      ],
      install_requires=read_requirements(),
      test_suite="",
      zip_safe=False
      )
