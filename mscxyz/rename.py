from fileloader import File

class Rename(File):

	def __init__(self, fullpath):
		super(Rename, self).__init__(fullpath)
		self.score = Meta(self.fullpath)
		self.workname = self.basename

	def replaceGermanUmlaute(self):
		umlaute = {'ae': u'ä', 'oe': u'ö', 'ue': u'ü', 'Ae': u'Ä', 'Oe': u'Ö', 'Ue': u'Ü'}
		for replace, search in umlaute.iteritems():
			self.workname = self.workname.replace(search, replace)

	def transliterate(self):
		import unidecode
		self.workname = unidecode.unidecode(self.workname)

	def replaceToDash(self, *characters):
		for character in characters:
			self.workname = self.workname.replace(character, '-')

	def deleteCharacters(self, *characters):
		for character in characters:
			self.workname = self.workname.replace(character, '')

	def cleanUp(self):
		string = self.workname
		string = string.replace('(', '_')
		string = string.replace('-_', '_')

		import re
		# Replace two or more dashes with one.
		string = re.sub('-{2,}', '_', string)
		string = re.sub('_{2,}', '_', string)
		# Remove dash at the begining
		string = re.sub('^-', '', string)
		# Remove the dash from the end
		string = re.sub('-$', '', string)

		self.workname = string

	def debug(self):
		print(self.workname)

	def prepareTokenSubstring(self, value, length):
		import unidecode
		import re
		value = value.lower()
		value = unidecode.unidecode(value)
		value = re.sub('[^A-Za-z]', '', value)
		return value[0:length]

	def getToken(self, token):
		title = self.score.get('title')
		if token == 'title_1char':
			return self.prepareTokenSubstring(title, 1)
		elif token == 'title_2char':
			return self.prepareTokenSubstring(title, 2)
		else:
			return self.score.get(token)

	def applyFormatString(self):
		import re
		output = args.format
		for token in re.findall('%(.*?)%', output):
			output = output.replace('%' + token + '%', self.getToken(token))

		self.workname = output

	def execute(self):
		if args.format:
			self.applyFormatString()

		if args.ascii:
			self.replaceGermanUmlaute()
			self.transliterate()

		if args.no_whitespace:
			self.replaceToDash(' ', ';', '?', '!', '_', '#', '&', '+', '/', ':')
			self.deleteCharacters(',', '.', '\'', '`', ')')
			self.cleanUp()

		if args.dry_run or args.verbose > 0:
			print(colored(self.basename, 'red') + ' -> ' + colored(self.workname, 'yellow'))

		if not args.dry_run:
			newpath = self.workname + '.' + self.extension
			create_dir(os.path.dirname(newpath))
			os.rename(self.fullpath, newpath)
