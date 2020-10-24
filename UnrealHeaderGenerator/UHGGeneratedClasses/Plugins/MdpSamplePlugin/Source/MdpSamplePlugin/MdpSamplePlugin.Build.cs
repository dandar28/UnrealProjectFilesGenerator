
using UnrealBuildTool;

public class MdpSamplePlugin : ModuleRules
{
	public MdpSamplePlugin(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"MdpCoreModule",
			"Core", 
			"CoreUObject",
			"Engine"
		});
		
		PrivateDependencyModuleNames.AddRange(new string[] {
		});
	}
}
