import tweepy

class MaxListener(tweepy.Stream):
    def on_data(self, raw_data):
        self.process_data(raw_data)
        
        return True
    
    def process_data(self, raw_data):
        print(raw_data)
    
    def on_error(self, status_code):
        if status_code == 420:
            return False
    
    

class MaxStream():
    def __init__(self, auth, listener, access_token, access_token_secret):
        self.stream = tweepy.Stream(auth=auth, listener=listener)
        
    def start(keywordList):
        self.stream.filter(track=keywordList)
        




if __name__ == "__main__":

    listener = MaxListener()
    auth = tweepy.OAuthHandler("UG5SdYVvFUllQjGmbaujH1sjE", "ZNTk1vEgLplByLIosOkJo7011a4OeTR9yeQsnS5hUFLawQnYsx")
    auth.set_access_token(access_token, access_token_secret)
    stream = MaxStream(auth, listener)
    stream.start(["Melbourne"])