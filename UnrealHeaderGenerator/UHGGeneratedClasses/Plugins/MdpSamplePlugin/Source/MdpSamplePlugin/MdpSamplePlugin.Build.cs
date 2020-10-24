
using UnrealBuildTool;

public class MdpSamplePlugin : ModuleRules
{
	public MdpSamplePlugin(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			MdpSamplePlugin,
			"Core", 
			"CoreUObject",
			"Engine"
		});
		
		PrivateDependencyModuleNames.AddRange(new string[] {
		});
	}
}
