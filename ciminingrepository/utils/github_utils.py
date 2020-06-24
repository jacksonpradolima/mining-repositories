import configparser

from github import Github

def auth_gh():
    '''
    A pattern to access the GitHab
    :param token:
    :return:
    '''
    config = configparser.ConfigParser()
    config.read('../../configuration.properties')

    # Github instance using an access token
    gh = Github(config['GitHub.com']['Token'])

    return gh
