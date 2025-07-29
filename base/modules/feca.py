
# File extention checker algorithm (feca)

# check extention of text in a list of extentions,
# return true or false accordingly
def check(string, extentions):
	index = string.index('.')
	string_extention = string[index:]

	if string_extention in extentions:
		return True
	else:
		return False

# Test [passed!]
# extentions = ['.txdt', '.jsx', '.mp3', '.bat']
# string = "song_hack.txt"

# print(f"Is {string} extention in extentions: {check(string, extentions)}")
