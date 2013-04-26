#encoding=utf-8
"""
Some helpful functions for parsing or changing Chinese text
"""
import re
import os
import subprocess
from HTMLParser import HTMLParser

import jieba
import jieba.posseg as pseg
import settings

from hanzidentifier import hanzidentifier

if settings.TRADITIONAL_DICT:
  print "Using traditional dictionary..."
  _curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
  if os.path.exists(os.path.join(_curpath, 'data/dict.txt.big')):
    jieba.set_dictionary('data/dict.txt.big')
  else:
    print "Warning: TRADITIONAL_DICT is enabled in settings, but the dictionary has not yet been downloaded. \n\nYou might want to try running download_data.py"

from jianfan import jtof as tradify, ftoj as simplify
to_traditional = tradify
to_simplified = simplify

known_punctuation = u'／（）、，。：「」…。『』！？《》'

def contains_ascii(unicode_string):
  """Attempts to determine whether the string contains any ASCII characters.
  
  Checks for any printable ASCII characters (0020-007E).

  It does not check for non-printable ASCII characters such as tabs and spaces,
    because those are often present in Chinese typing as well.

  """
  if re.search(ur'[\u0020-\u007E]', unicode_string) is None:
      return False
  else:
      return True


def has_punctuation(word):
  """
  Check if a string has any of the common Chinese punctuation marks.
  """
  if re.search(r'[%s]' % known_punctuation, word) is not None:
      return True
  else:
      return False


def iconv(text, args):
  p1 = subprocess.Popen(["echo", text], stdout=subprocess.PIPE)
  p2 = subprocess.Popen(['iconv'] + list(args), stdout=subprocess.PIPE, stdin = p1.stdout, stderr=subprocess.STDOUT)
  p1.stdout.close()
  output = p2.communicate()[0]
  print output
  return output

def identify(text):
  """
  Wrapper for hanzidentifier identify function

  Returns:
    None: if there are no recognizd Chinese characters.
    EITHER: if the test is inconclusive.
    TRAD: if the text is traditional.
    SIMP: if the text is simplified.
    BOTH: the text has characters recognized as being solely traditional
        and other characters recognized as being solely simplified.
  """
  return hanzidentifier.identify(text)

def is_simplified(text):
  """
  Determine whether a text is simplified Chinese
  Returns True if written in Simplified, False otherwise.

  Note: This assumes the text is known to be one or the other.
  """
  return hanzidentifier.identify(text) is hanzidentifier.SIMP

def is_traditional(text):
  """
  Determine whether a text is simplified Chinese
  Returns True if written in Simplified, False otherwise.

  Note: This assumes the text is known to be one or the other.
  """
  return hanzidentifier.identify(text) is hanzidentifier.TRAD


def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def split_text(text, include_part_of_speech=False, strip_english=False, strip_numbers=False):
  """
  Split Chinese text at word boundaries.

  include_pos: also returns the Part Of Speech for each of the words.
  Some of the different parts of speech are:
    r: pronoun
    v: verb
    ns: proper noun
    etc...

  This all gets returned as a tuple:
    index 0: the split word
    index 1: the word's part of speech

  strip_english: remove all entries that have English or numbers in them (useful sometimes)
  """
  # was_traditional = is_traditional(text)
  # string = text

  # if was_traditional:
  #   string = simplify(string)

  if not include_part_of_speech:
    seg_list = jieba.cut_for_search(text)
    if strip_english:
      seg_list = filter(lambda x: not contains_english(x), seg_list)
    if strip_numbers:
      seg_list = filter(lambda x: not _is_number(x), seg_list)
    return list(seg_list)
  else:
    seg_list = pseg.cut(text)
    objs = map(lambda w: (w.word, w.flag), seg_list)
    if strip_english:
      objs = filter(lambda x: not contains_english(x[0]), objs)
    if strip_english:
      objs = filter(lambda x: not _is_number(x[0]), objs)
    return objs

  # if was_traditional:
  #   seg_list = map(tradify, seg_list)

  return list(seg_list)
