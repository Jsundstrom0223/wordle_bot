import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

word_list = pd.read_csv("split_list.csv", header=None, index_col=0)


wordle_url = "https://www.nytimes.com/games/wordle/index.html"
driver = webdriver.Firefox()
play_button = "Welcome-module_button__ZG0Zh"
driver.get(wordle_url)
elem = driver.find_element(By.CLASS_NAME, play_button)

elem.send_keys(Keys.RETURN)
x_button = driver.find_element(By.CLASS_NAME, "Modal-module_closeIcon__TcEKb")
x_button.click()
page = driver.find_element(By.ID, "wordle-app-game")
body = driver.find_element(By.XPATH, "//body")
time.sleep(4)

LETTERS1 = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
LETTERS2 = ["a", "s", "d", "f", "g", "h", "j", "k", "l"]
LETTERS3 = ["z", "x", "c", "v", "b", "n", "m"]
ALL_LETTERS = [LETTERS1, LETTERS2, LETTERS3]

ROW1 = f"/html/body/div/div/div[2]/div/div[2]/div[1]/button"
ROW2 = f"/html/body/div/div/div[2]/div/div[2]/div[2]/button"
ROW3 = f"/html/body/div/div/div[2]/div/div[2]/div[3]/button"
ROW_DICT = {ROW1: LETTERS1, ROW2: LETTERS2, ROW3: LETTERS3}

class Letters():
  path_dict = {}
  guessed_letters = []
  to_check = []

  def __init__(self, name, ind_in_guess, path, outcome=None, actual_ind=None):
    self.name = name
    self.ind_in_guess = ind_in_guess + 1
    self.path = path
    self.outcome = outcome
    self.actual_ind = None
 
    Letters.path_dict[self] = self.path

def find_location(letter):
  path = None
  for row, letter_list in ROW_DICT.items():

    if letter in letter_list:
      if row == ROW3:
        kb_index = letter_list.index(letter) + 2
      else:
        kb_index = letter_list.index(letter) + 1
      path = f"{row}[{kb_index}]"
     
      return path
    
def find_correct_letters(word):
  present = {}
 
  for w in word:
    found_letter = driver.find_element(By.XPATH, w.path)
    state = found_letter.get_attribute("aria-label")
    print(w.name, state, w.path, "\n\n")
    if "correct" in state:
      w.outcome = "correct"
      w.actual_ind = w.ind_in_guess
    if "absent" in state:
      w.outcome = "absent"
    if "present" in state:
      present[w.ind_in_guess] = w.name
      w.outcome = "present"

def make_guess(guess):
  body.send_keys(guess)
  body.send_keys(Keys.RETURN)
  time.sleep(8)

  for ind, let in enumerate(guess): 
    if Letters.path_dict.get(let) == None:
      path = find_location(let)
      Letters.guessed_letters.append(Letters(let, ind, path))
      
  find_correct_letters(Letters.guessed_letters)

def apply_outcome(avail_words):
  for letter in Letters.guessed_letters:
    if letter.outcome == "correct":
      avail_words = avail_words.loc[avail_words[letter.actual_ind] == letter.name]
      
    if letter.outcome == "absent":
      avail_words = avail_words.loc[~avail_words.eq(letter.name).any(axis=1)]

    if letter.outcome == "present":
      avail_words = avail_words.loc[avail_words[letter.ind_in_guess] != letter.name]

  return avail_words

print("PRE_RUN wordlist length = ", word_list.shape)
make_guess("stark")
word_list = apply_outcome(word_list)
print("FIRST GUESS wordlist length = ", word_list.shape)
time.sleep(10)
make_guess("trace")
word_list = apply_outcome(word_list)
print("SECOND GUESS wordlist length = ", word_list.shape)
word_list.to_csv("words_as_csv.csv")

time.sleep(10)
driver.close()
