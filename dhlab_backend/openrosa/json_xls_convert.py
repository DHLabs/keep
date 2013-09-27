import re

from openpyxl import Workbook

class jsonXlsConvert():
	'''
	def __init__(self, file_name): 
		self.xlsFileName = file_name + ".xls"
		self.bindDict = {}
		self.questionDict = {}

	def getBindDict(self, jsonDict):
		for element in jsonDict:
			if "bind" in element:
				stuff

				if element["type"] == 'group':
					self.getBindDict(self, element)
	'''

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

	'''Utility function to write an array to excel using openpyxl'''
	def writeArrayToXLS(worksheet, array_to_write, starting_cell, horizontal=True):
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


