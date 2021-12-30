from more_itertools import split_after
import csv
import argparse
import re

def parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('vcf_file')
	parser.add_argument('csv_output')
	args = parser.parse_args()
	write_csv(args.vcf_file, args.csv_output)


def write_csv(vcard_file, csv_output):
	'''Write CSV file.'''
	filename = csv_output

	with open(filename, "w", errors='ignore') as csvfile:
		fieldnames = ["Title","First Name","Middle Name","Last Name","Suffix","Company","Department","Job Title","Business Street",
		"Business Street 2","Business Street 3","Business City","Business State","Business Postal Code","Business Country/Region",
		"Home Street","Home Street 2","Home Street 3","Home City","Home State","Home Postal Code","Home Country/Region","Other Street",
		"Other Street 2","Other Street 3","Other City","Other State","Other Postal Code","Other Country/Region","Assistant's Phone",
		"Business Fax","Business Phone","Business Phone 2","Callback","Car Phone","Company Main Phone","Home Fax","Home Phone","Home Phone 2",
		"ISDN","Mobile Phone","Other Fax","Other Phone","Pager","Primary Phone","Radio Phone","TTY/TDD Phone","Telex","Account","Anniversary",
		"Assistant's Name","Billing Information","Birthday","Business Address PO Box","Categories","Children","Directory Server","E-mail Address"
		,"E-mail Type","E-mail Display Name","E-mail 2 Address","E-mail 2 Type","E-mail 2 Display Name","E-mail 3 Address","E-mail 3 Type",
		"E-mail 3 Display Name","Gender","Government ID Number","Hobby","Home Address PO Box","Initials","Internet Free Busy","Keywords","Language",
		"Location","Manager's Name","Mileage","Notes","Office Location","Organizational ID Number","Other Address PO Box","Priority","Private",
		"Profession","Referred By","Sensitivity","Spouse","User 1","User 2","User 3","User 4","Web Page"]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		csvwriter=csv.writer(csvfile)
		csvwriter.writerow(fieldnames)
		dictionary_list = (separate_vcards(vcard_file))
		for dictionary in dictionary_list:
			print(dictionary)
			writer.writerow(dictionary)

def separate_vcards(vcard_file):
	'''Open vCard file and separate individual vCards.''' 
	vcf = open(vcard_file, encoding="utf8")
	lines = vcf.readlines()
	vcard_list = (list(split_after(lines, lambda x: x.startswith("END:VCARD"))))
	dictionary_list = []
	for vcard in vcard_list:
		dictionary_list.append(get_vcard_info(vcard))
	return dictionary_list
		

def get_vcard_info(vcard):
	'''Check vCard version and call appropriate function.'''
	if "VERSION:3.0\n" in vcard:
		return get_3_0_info(vcard)
	elif "VERSION:2.1\n" in vcard:
		return get_2_1_info(vcard)
	else:
		print("This vCard version is not supported.")

def get_2_1_info(vcard):
	'''Scrapes info from version 2.1 vCard files'''
	dictionary = {}
	for line in vcard:	
		if "FN" in line:
			try:
				full_name = line.split(':')[1]
				first_name = full_name.split()[0]
				last_name = full_name.split(' ',1)[1]
				dictionary["First Name"] = first_name.rstrip()
				dictionary["Last Name"] = last_name.rstrip()
			except:
				IndexError
				try:
					full_name = line.split(':')[1]
					first_name = full_name.split()[0]
					dictionary["First Name"] = first_name.rstrip()
				except:
					#Address unusual characters or name entries
					UnboundLocalError
					continue
		elif "CELL" in line:
			cell_phone = line.split(':')[1]
			dictionary["Mobile Phone"] = cell_phone.rstrip()
		elif "WORK;VOICE" in line:
			work_phone = line.split(':')[1]
			dictionary["Business Phone"] = work_phone.rstrip()
		elif "EMAIL" in line:
			email = line.split(':')[1]
			dictionary["E-mail Address"] = email.rstrip()
	return dictionary 

def get_3_0_info(vcard):
	dictionary = {}
	emails = []
	phonenums = []
	'''Scrapes info from version 3.0 vCard files'''
	for line in vcard:
		if re.search("^N:", line):
			if "N:;;;;" in line:
				for line in vcard:
					if "FN:" in line:
						first_name = line.split(':', 1)[1]
						dictionary["First Name"] = first_name.strip()
			else:
				try:
					full_name = line.split(':', 1)[1]
					first_name1 = full_name.split(';', 1)[1]
					first_name = first_name1.replace(';', '')
					last_name1 = full_name.split(';', 1)[0]
					last_name = last_name1.replace(';', '')
					dictionary["First Name"] = first_name.strip()
					dictionary["Last Name"] = last_name.strip()
				except:
					IndexError
					if "FN" in line:
						first_name = line.split(':', 1)[1]
						dictionary["First Name"] = first_name.strip()
		if "ORG" in line:
			company = line.split(":")[1]
			company1 = company.replace(';', '')
			dictionary["Company"] = company1.strip()
		if "TITLE" in line:
			title = line.split(':')[1]
			dictionary["Job Title"] = title.strip()
		if "TEL" in line:
			if "type=HOME" in line:
				home_phone = line.split(':')[1]
				dictionary["Home Phone"] = home_phone.rstrip()
			elif "type=CELL" in line:
				cell_phone = line.split(':')[1]
				dictionary["Mobile Phone"] = cell_phone.rstrip()
			elif "type=WORK" in line:
				work_phone = line.split(':')[1]
				dictionary["Business Phone"] = work_phone.rstrip()
			elif "type=FAX" in line:
				fax = line.split(':')[1]
				dictionary["Other Fax"] = fax.rstrip()
			else:
				phone = line.split(":")[1]
				phonenums.append(phone)
		if len(phonenums) == 2:
			dictionary["Other Phone"] = phonenums[0].rstrip()
			dictionary["Mobile Phone"] = phonenums[1].rstrip()
		if len(phonenums) == 1:
			dictionary["Other Phone"] = phonenums[0].rstrip()
		if "EMAIL" in line:
			email = line.split(":")[1]
			emails.append(email)
			if len(emails) == 3:
				dictionary["E-mail Address"] = emails[0].strip()
				dictionary["E-mail 2 Address"] = emails[1].strip()
				dictionary["E-mail 3 Address"] = emails[2].strip()
			elif len(emails) == 2:
				dictionary["E-mail Address"] = emails[0].strip()
				dictionary["E-mail 2 Address"] = emails[1].strip()
			elif len(emails) == 1:
				dictionary["E-mail Address"] = emails[0].strip()
	return dictionary

if __name__ == "__main__":
	parse()

