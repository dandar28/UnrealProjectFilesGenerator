
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
% for curModuleName in UHGModule.data["PublicDependencyModuleNames"]:
			"${curModuleName}",
% endfor
			"Core", 
			"CoreUObject",
			"Engine"
		});
		
		PrivateDependencyModuleNames.AddRange(new string[] {
% for curModuleName in UHGModule.data["PrivateDependencyModuleNames"]:
			"${curModuleName}",
% endfor
		});
	}
}
''';

	return templateName, templateContent, className