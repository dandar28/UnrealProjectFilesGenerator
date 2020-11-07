
def GetTemplateInfo():
	className = 'U${name}'
	templateName = 'UObject'
	templateContent = '''
#pragma once

// unreal headers
#include "CoreMinimal.h"

% if 'includes' in TemplateData.data:
// custom headers
% for include in TemplateData.data["includes"]:
#include "${Settings.GetIncludePath(include)}"
% endfor
% endif

// generated headers
#include "${className}.generated.h"

UCLASS(${metadata["uclass"] if 'uclass' in metadata else ''})
class ${className} : public UObject {
	GENERATED_CLASS()	
public:
% for member in members:
	UPROPERTY(${member["metadata"]})
	${member["declaration"]};

% endfor

% for func in functions:
	UFUNCTION(${func["metadata"]})
	${func["declaration"]};

% endfor
};

// using ${namespace}::U${TemplateData.GetAlias()} = ${className};
''';

	return templateName, templateContent, className