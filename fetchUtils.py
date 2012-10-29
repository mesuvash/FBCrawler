from errors import FBApiCallError
import urllib
import json


def isError(response):
    """
    Facebook returns json with error key when error occurs
    """
    return True if "error" in response else False


def fb_call(call, args=None, no_processing=False):
    """`
    Call graph API
    """

    if not no_processing:
        url = "https://graph.facebook.com/{0}".format(call)
        params = urllib.urlencode(args)
        request = (url + "?%s") % params
    else:
        request = call
    response = urllib.urlopen(request).read()
    json_response = json.loads(response)
    if isError(json_response):
        raise FBApiCallError(call + json_response)
    return json_response


def get_fb_likes(uid, access_token, limit=1000):
    """
    Call graph api to get user's likes information
    """
    def get_fb_likes_recursively(response):
        if "next" in response["paging"]:
            _response = fb_call(response["paging"]["next"],
                                no_processing=True)
            return response["data"] + get_fb_likes_recursively(_response)
        else:
            return response["data"]

    query = "%s/likes" % uid
    response = fb_call(query, args={"access_token": access_token, "limit": limit})
    return get_fb_likes_recursively(response)


def get_fb_basic_info(uid, access_token):
    """
    Call graph api to get user's basic information
    """
    return fb_call(uid, args={"access_token": access_token})
