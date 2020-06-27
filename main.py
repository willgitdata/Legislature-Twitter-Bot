# Imports Everything that is Needed
import requests
import urllib.request
import time
import tweepy
from datetime import datetime, timedelta
from selenium import webdriver
import chromedriver_binary
from flask import Flask, send_file


app = Flask(__name__)

@app.route("/")
def selenium_twitter_bot():


	# Set all static variables
	# Create variables for each key, secret, token
	consumer_key = 'KPWV43OLrh2l1sHmyz6vos9rB'
	consumer_secret = 's6mMommXjf1c3HOrFPJ9DF0GddVNu6x5WpIEmWbKkAzVytdZeh'
	access_token = '1242097568856842242-gk90remwWj3K9EyX1PXNz3qeALjCZe'
	access_token_secret = 'qxIwoOGPjI1l8F4TLXETQMqX2krimPMWKfiHn8991AIg4'

	# Set up OAuth and integrate with API
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	year = datetime.now().year 
	congress = int(((year + 1)/2) - 894)
	session = 1 if year % 2 else 2
	yesterday = datetime.date(datetime.now()) - timedelta(1)
	house_url = "http://clerk.house.gov/evs/{}/index.asp".format(year)
	senate_url = "https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_{}_{}.htm".format(congress, session)

	# Set custom options
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	options.add_argument("window-size=1024,768")
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-gpu')


	

	# Boot our drivers with the custom options
	house_driver = webdriver.Chrome(options = options)
	senate_driver = webdriver.Chrome(options = options)
	helper_driver = webdriver.Chrome(options = options)

	#Navigate to the URLS
	house_driver.get(house_url)
	senate_driver.get(senate_url)
	time.sleep(10)

	# House section
	house_votes = house_driver.find_elements_by_tag_name('tr')

	for i in range(len(house_votes)):
		if not i:
			continue
		vote_array = house_votes[i].find_elements_by_tag_name('td')
		url = vote_array[2].find_element_by_tag_name('a').get_attribute('href')
		description = vote_array[5].text 
		question = vote_array[3].text
		result = "Passed" if vote_array[4].text == "P" else "Failed"
		tweet = "New vote {} in the House\n\nQuestion:{}\n\nDescription: {}\n\nVote: {}" \
						.format(yesterday.strftime("%m/%d/%Y"), question, description, result)
		# Checker if the tweet is too long
		if (len(tweet) > 280):
			description = "{}\nSee {} for more" \
										.format( vote_array[2].text, url)
			tweet = "New vote {} in the House\n\nQuestion: {}\n\nDescription: {}\n\nVote: {}" \
							.format(yesterday.strftime("%m/%d/%Y"), question, description, result)
		api.update_status(status=tweet)
		time.sleep(5)

	# Senate section
	senate_votes = senate_driver.find_elements_by_tag_name('tr')
	for i in range(len(senate_votes)):
		if not i:
			continue
		vote_array = senate_votes[i].find_elements_by_tag_name('td')
		if (yesterday.strftime("%b %d") != vote_array[4].text):
			break
		tally = vote_array[0].text.split()[1]
		result = vote_array[1].text
		url = vote_array[0].find_element_by_tag_name('a').get_attribute('href')
		question = 'Question: ' + vote_array[2].text.split(':', 1)[0]
		description = "Description: " + vote_array[2].text.split(':', 1)[1]
		tweet = "New vote {} in the Senate\n\n{}\n\n{}\n\nVote: {} {}" \
						.format(yesterday.strftime("%m/%d/%Y"), question, description, result, tally)
		if (len(tweet) > 280):
			helper_driver.get(url)
			time.sleep(5)
			body = helper_driver.find_element_by_class_name('contenttext')
			body = body.find_elements_by_tag_name('div')
			description = body[-1].text
			tweet = "New vote {} in the Senate\n\n{}\n\n{}\n\nVote: {} {}" \
					.format(yesterday.strftime("%m/%d/%Y"), question, description, result, tally)
		if(len(tweet) > 280):
			description = "{}\nSee more at {}".format(body[0].text, url)
			tweet = "New vote {} in the Senate\n\n{}\n\nVote: {} {}" \
					.format(yesterday.strftime("%m/%d/%Y"), description, result, tally)
		api.update_status(status=tweet)
		time.sleep(5)

	helper_driver.get("https://www.google.com/search?client=firefox-b-1-d&q=smiley+face")
	helper_driver.save_screenshot("happy.png")
	return send_file("happy.png")
