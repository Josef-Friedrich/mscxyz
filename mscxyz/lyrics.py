# -*- coding: utf-8 -*-

"""Manipulate the lyrics"""

from tree import Tree

class Lyrics(Tree):

	def __init__(self, fullpath, args):
		super(Lyrics, self).__init__(fullpath, args)
		self.lyrics = self.normalizeLyrics()
		self.max = self.getMax()

	def normalizeLyrics(self):
		lyrics = []
		for lyric in self.tree.findall('.//Lyrics'):
			safe = {}
			safe['element'] = lyric
			number = lyric.find('no')

			if hasattr(number, 'text'):
				no = int(number.text) + 1
			else:
				no = 1
			safe['number'] = no

			lyrics.append(safe)

		return lyrics

	def getMax(self):
		max_lyric = 0
		for element in self.lyrics:
			if element['number'] > max_lyric:
				max_lyric = element['number']

		return max_lyric

	def remap(self):
		for pair in self.args.remap.split(','):
			old = pair.split(':')[0]
			new = pair.split(':')[1]
			for element in self.lyrics:
				if element['number'] == int(old):
					element['element'].find('no').text = str(int(new) - 1)

		self.write()

	def extractOneLyricVerse(self, number):
		score = Lyrics(self.fullpath, self.args)

		for element in score.lyrics:
			tag = element['element']

			if element['number'] != number:
				tag.getparent().remove(tag)
			elif number != 1:
				tag.find('no').text = '0'

		ext = '.' + self.extension
		new_name = score.fullpath.replace(ext, '_' + str(number) + ext)
		score.write(new_name)

	def extractLyrics(self, number=None):
		if number:
			self.extractOneLyricVerse(int(number))
		else:
			for number in range(1, self.max + 1):
				self.extractOneLyricVerse(number)

	def fixLyrics(self):
		"""
		from:

			<Lyrics>
				<text>la-</text>
			</Lyrics>
			<Lyrics>
				<syllabic>end</syllabic>
				<text>la-</text>
			</Lyrics>
			<Lyrics>
				<text>la.</text>
			</Lyrics>

		to:

			<Lyrics>
				<syllabic>begin</syllabic>
				<text>la</text>
			</Lyrics>
			<Lyrics>
				<syllabic>middle</syllabic>
				<text>la</text>
			</Lyrics>
			<Lyrics>
				<syllabic>end</syllabic>
				<text>la.</text>
			</Lyrics>
		"""
		import lxml.etree as etree

		syllabic = False
		for element in self.lyrics:
			tag = element['element']
			tag_text = tag.find('text')
			text = tag_text.text
			tag_syl = etree.Element('syllabic')
			if text.endswith('-'):
				tag_text.text = text[:-1]
				if not syllabic:
					tag_syl.text = 'begin'
					syllabic = True
				else:
					tag_syl.text = 'middle'
			else:
				if syllabic:
					tag_syl.text = 'end'
					syllabic = False
				else:
					tag_syl = False
			tag.append(tag_syl)
			self.write()
