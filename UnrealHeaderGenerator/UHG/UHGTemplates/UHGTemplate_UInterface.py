
def GetTemplateInfo():
	className = 'I${name}Interface'
	templateName = 'UInterface'
	templateContent = '''
#pragma once

// unreal headers
#include "CoreMinimal.h"

// generated headers
#include "${className}.generated.h"

UINTERFACE(${metadata["uinterface"] if 'uinterface' in metadata else ''})
class ${Settings.GetAPI()} U${name}Interface : public UInterface {
	GENERATED_UINTERFACE_BODY()
};

class I${name}Interface {
	GENERATED_IINTERFACE_BODY()	
public:

% for func in functions:
	UFUNCTION(${func["metadata"]})
	${func["declaration"]};

% endfor
};

// using ${namespace}::I${name} = I${name}Interface;
''';

	return templateName, templateContent, className