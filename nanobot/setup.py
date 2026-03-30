from setuptools import setup, find_packages

setup(
    name="nanobot-webchat",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "nanobot-ai>=0.1.4.post6",
        "websockets>=12.0",
    ],
    entry_points={
        'nanobot.channels': [
            'webchat = nanobot_webchat.channel:WebChatChannel',
        ],
    },
)
