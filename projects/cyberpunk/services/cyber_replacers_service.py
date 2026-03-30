import re
import random
import logging 

class CyberReplacersService:
    def __init__(self):
        self.whats_your_angle_lines = []
        self.save_your_breath_lines = []
        self.sweetheart_replace_lines = []
        self.spare_me_line_replace_lines = []
        self.are_you_kidding_line_replace_lines = []

    def whats_your_angle_line(self):
        if not self.whats_your_angle_lines:
            self.whats_your_angle_lines = [
                "What's your perspective",\
                "What’s your viewpoint",\
                "What’s your take",\
                "How do you see it",\
                "What’s your side",\
                "What’s your position",\
                "What’s your interpretation",\
                "What’s your take",\
                "What’s your point",\
                "What's your vibe",\
                "What do you think",\
                "What’s going on",\
                "What’s your hustle",\
                "What’s the gist",\
                "What's the scoop",\
                "What’s the lowdown",\
                "What’s your move",\
                "What’s on your mind",\
                "What’s your game plan",\
                "What’s your focus",\
                "What’s your reason",\
                "What’s your aim",\
                "What’s your objective",\
                "What’s your angle on this",\
                "What’s your opinion",\
                "What’s the deal here",\
                "What’s your thought process",\
                "What’s your insight",\
                "What are you thinking",
            ]
        return self.whats_your_angle_lines[random.randrange(0, len(self.whats_your_angle_lines))]

    def save_your_breath_line(self):
        if not self.save_your_breath_lines:
            self.save_your_breath_lines = [
                "Don't waste your time",
                "Don't trouble yourself",
                "Spare yourself",
                "Don't say anything",
                "Don't say nothing",
                "Don't trouble yourself",
                "Don't waste your time",
                "Spare the effort",
                "Dom't bother",
                "Don't waste your words",
                "Do not waste time",
                "It's not worth talking about",
                "Don't waste your breath",
                "It is not worth talking",
                "It's not worth talking",
                "Useless to talk",
                "keep it to yourself",
                "Don't bother saying anything",
                "don't even bother",
                "Shut up",
                "Shut the fuck up",
                "Stop talking",
                "This is absolute bullshit",
                "Bullshit",
                "Just shut your mouth",
                "Shut your mouth",
                "Keep it to yourself",
                "Quit the act"
            ]
        return self.save_your_breath_lines[random.randrange(0, len(self.save_your_breath_lines))]

    def spare_me_line_replace_line(self):
        if not self.spare_me_line_replace_lines:
            self.spare_me_line_replace_lines = [
                "Quit the bullshit",
                "Stop acting",
                "Stop shitting me",
                "You are lying",
                "Bullshit",
                "Not true",
                "Thats garbage",
                "Stop the act",
                "Quit the act"
            ]
        return self.spare_me_line_replace_lines[random.randrange(0, len(self.spare_me_line_replace_lines))]
    
    def sweetheart_replace_line(self):
        if not self.sweetheart_replace_lines:
            self.sweetheart_replace_lines = [
                "cutie", 
                "gorgeous", 
                "handsome",
                "beautiful",
                "sweetheart",
                "honey",
                "charm", 
                "spark", 
                "sunshine",
                "choomba",
                "choom"
            ]
        return self.sweetheart_replace_lines[random.randrange(0, len(self.sweetheart_replace_lines))]
    

    def are_you_kidding_line_replace_line(self):
        if not self.are_you_kidding_line_replace_lines:
            self.are_you_kidding_line_replace_lines = [
                "Are you serious",
                "Really",
                "Are you sure",
                "Are you shitting me",
                "Are you out of your mind",
                "Are you fucking with me",
                "Is this real",
                "Oh my god!"                
            ]
        return self.are_you_kidding_line_replace_lines[random.randrange(0, len(self.are_you_kidding_line_replace_lines))]