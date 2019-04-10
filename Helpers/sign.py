#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Signs a URL using a URL signing secret """
##对签名进行验证代码
import hashlib
import hmac
import base64
import urllib.parse

def sign_url(input_url=None, secret=None):
  """ Sign a request URL with a URL signing secret.
      Usage:
      from urlsigner import sign_url
      signed_url = sign_url(input_url=my_url, secret=SECRET)
      Args:
      input_url - The URL to sign
      secret    - Your URL signing secret
      Returns:
      The signed request URL
  """

  if not input_url or not secret:
    raise Exception("Both input_url and secret are required")

  url = urllib.parse.urlparse(input_url)

  # We only need to sign the path+query part of the string
  url_to_sign = url.path + "?" + url.query
  # Decode the private key into its binary format
  # We need to decode the URL-encoded private key
  decoded_key = base64.urlsafe_b64decode(secret)
  # Create a signature using the private key and the URL-encoded
  # string using HMAC SHA1. This signature will be binary.
  signature = hmac.new(decoded_key, url_to_sign.encode('utf-8'), hashlib.sha1)
  # Encode the binary signature into base64 for use within a URL
  encoded_signature = base64.urlsafe_b64encode(signature.digest())

  original_url = url.scheme + "://" + url.netloc + url.path + "?" + url.query

  # Return signed URL
  bytes.decode(encoded_signature)
  #str(encoded_signature,encoding='utf-8')
  return original_url,encoded_signature

if __name__ == "__main__":
  #input_url = input("URL to Sign: ")
  input_url='https://maps.googleapis.com/maps/api/staticmap?center=39.93944692354029,116.39745889999995&zoom=11&format=png&maptype=roadmap&size=480x360&key=AIzaSyAadVAdjp_hGd21y9y-R6wQ0IcOcHcrl9c'
  #secret = input("URL signing secret: ")
  secret='Bfmu0RYkRyvVwZP5DGV8FqKdKfI='
  a,b=sign_url(input_url, secret)
  c=a + "&signature=" + bytes.decode(b)
  print (c)
