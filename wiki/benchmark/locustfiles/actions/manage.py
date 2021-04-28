import json

import actions.common as common
import actions.graphqlQueries as graphqlQueries


def applySettings(httpUser):
    # Apply comments settings
    comments_settings = json.loads(common.readFile("settings/comments.json"))
    graphqlQueries.updateCommentsSettings(httpUser, comments_settings)

    # Apply security settings
    security_settings = json.loads(common.readFile("settings/security.json"))
    graphqlQueries.updateSecuritySettings(httpUser, security_settings)