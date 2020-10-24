
#include "MdpCoreModule_PrivatePCH.h"

class FMdpCoreModule : public IMdpCoreModule
{
	virtual void StartupModule() override
	{
	}

	virtual void ShutdownModule() override
	{
	}
};

IMPLEMENT_MODULE( FMdpCoreModule, MdpCoreModule )
