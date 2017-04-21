# Mnemonic
Mnemonic is a social memory companion that uses IBM Watson's AlchemyLanguage API and Microsoft Cognitive Service API to keep track of all the people a user meets.

# How we built it
There are three main components of Mnemonic: an iOS app, a Linode server, and a Raspberry Pi. When a user first meets someone, the user triggers the start of the process by pushing a button on a breadboard. This push triggers the camera of the Raspberry Pi to take three photos of the person that is met. This also sends information to the server. The iOS app constantly sends post requests to the Linode server to see whether an action is required. If one is, it either matches the photos to an existing profile using Microsoft Cognitive Services Face API, in which case the app will pull up the existing profile, or it will create a new profile by recording the audio of the conversation. Using IBM Watson's AlchemyLanguage API, we analyze this data for any relevant keywords, using these as keyword topics to be stored in that person's profile. The user can use this information to more easily recall the person the next time that person is seen again.

- [x] use github markdown pamphlet
---
Made by Daniel, Josh, Avery, Arlene.
:rocket: :rocket: :rocket:
