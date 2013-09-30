import re

from openpyxl import Workbook

class jsonXlsConvert():
	#def __init__(self): 
	#	pass


	def writeToXls(self, json_dict, file_name):
		wb = Workbook()
		worksheet1 = wb.get_active_sheet()
		worksheet1.title = 'survey'
		surveyHeaders = ['type', 'name', 'label', 'hint', 'media::image',
						 'media::video', 'media::audio', 'constraint', 
						 'constraint_message', 'required', 'default', 
						 'relevant', 'read_only', 'calculation', 'appearance']
		self.writeArrayToXLS(worksheet1, surveyHeaders, 'A1')

		worksheet2 = wb.create_sheet(1)
		worksheet2.title = 'choices'
		choicesHeaders = ['list name', 'name', 'label', 'image']
		self.writeArrayToXLS(worksheet2, choicesHeaders, 'A1')

		self.recurseWriter(json_dict, worksheet1, worksheet2, surveyHeaders, choicesHeaders)

		return wb.save(file_name + '.xls')

	def recurseWriter(self, json_dict, wb1, wb2, wb1Headers, wb2Headers):
		iterRow = 1
		choicesRow = 1
		for element in json_dict:
			iterRow += 1
			surveyWriteRow = []

			if element.get("type") == 'group':
				surveyWriteRow = ['begin group']
				self.writeArrayToXLS(wb1, surveyWriteRow, ('A' + `iterRow`))
				self.recurseWriter(element.get("children"), wb1, wb2, wb1Headers, wb2Headers)
				iterRow += 1
				surveyWriteRow = ['end group']
				self.writeArrayToXLS(wb1, surveyWriteRow, ('A' + `iterRow`))

			else:
				for header in wb1Headers:
					if header in element:
						surveyWriteRow += [element.get(header)]
					else:
						surveyWriteRow += [""]
				self.writeArrayToXLS(wb1, surveyWriteRow, ('A' + `iterRow`))

			if 'choices' in element:
				choiceOptions = element['choices']
				choicesRow += 1
				choiceWriteRow = []
				for choice in choiceOptions:
					for header in wb2Headers:
						if header in choice:
							choiceWriteRow += [choice.get(header)]
						else:
							choiceWriteRow += [""]
					self.writeArrayToXLS(wb2, choiceWriteRow, ('A' + `choicesRow`))
					choiceWriteRow = []

	'''Utility function to write an array to excel using openpyxl'''
	def writeArrayToXLS(self, worksheet, array_to_write, starting_cell, horizontal=True):
		res = re.findall(r'\d+', starting_cell)

		row = res[0]
		col = starting_cell[:-len(res[0])]
		col_ind = ord(col) - 96 + 32 # only works for A-Z in caps

		if horizontal:
			for i in range(0,len(array_to_write)):
				cell_str = '%s%d' % (chr(col_ind + 64 + i), int(row))
				worksheet.cell(cell_str).value = array_to_write[i]
				# print cell_str

		else:
			for i in range(0,len(array_to_write)):
				cell_str = '%s%d' % (chr(col_ind + 64 ), int(row) + i)
				worksheet.cell(cell_str).value = array_to_write[i]
				# print cell_str

