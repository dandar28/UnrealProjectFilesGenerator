
def GetTemplateInfo():
	className = '${name}'
	templateName = 'Module'
	templateContent = '''
using UnrealBuildTool;

public class ${moduleName} : ModuleRules
{
	public ${moduleName}(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
% for func in UHGModule.data["PublicDependencyModuleNames"]:
			${moduleName},
% endfor
			"Core", 
			"CoreUObject",
			"Engine"
		});
		
		PrivateDependencyModuleNames.AddRange(new string[] {
% for func in UHGModule.data["PrivateDependencyModuleNames"]:
			${moduleName},
% endfor
		});
	}
}
''';

	return templateName, templateContent, className