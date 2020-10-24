
#pragma once
#include "ModuleManager.h"

class MdpCoreModule : public IModuleInterface
{
public:
	static inline IMdpCoreModule& Get()
	{
		return FModuleManager::LoadModuleChecked<IMdpCoreModule>("MdpCoreModule");
	}

	static inline bool IsAvailable()
	{
		return FModuleManager::Get().IsModuleLoaded("MdpCoreModule");
	}
};
