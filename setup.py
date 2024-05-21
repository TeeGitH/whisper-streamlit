from setuptools import setup, find_packages

setup(
    name='speech_transcription_app',  # Name of your package
    version='0.1',  # Version of your package
    packages=find_packages(),  # Automatically find packages in your project
    include_package_data=True,  # Include non-code files specified in MANIFEST.in
    install_requires=[  # List of dependencies to install with your package
        'streamlit==1.11.0',
        'openai==0.27.0',
        'python-dotenv==0.19.2',
        'audio-recorder-streamlit==0.1.5',
    ],
    entry_points={  # Define entry points for command-line scripts
        'console_scripts': [
            'transcribe=speech_transcription_app:main',  # Command to run main function from speech_transcription_app module
        ],
    },
)