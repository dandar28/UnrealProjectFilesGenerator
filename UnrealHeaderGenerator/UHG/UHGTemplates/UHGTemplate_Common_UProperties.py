
def GetTemplateInfo():
	templateName = 'UProperty'
	templateContent = '''
	UPROPERTY(${propertyData["metadata"]})
	${propertyData["declaration"]};
''';

	return templateName, templateContent, None