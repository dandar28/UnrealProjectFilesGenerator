
#pragma once
#include "ModuleManager.h"

class MdpSamplePlugin : public IModuleInterface
{
public:
	static inline IMdpSamplePlugin& Get()
	{
		return FModuleManager::LoadModuleChecked<IMdpSamplePlugin>("MdpSamplePlugin");
	}

	static inline bool IsAvailable()
	{
		return FModuleManager::Get().IsModuleLoaded("MdpSamplePlugin");
	}
};
