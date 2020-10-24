
#include "MdpSamplePlugin_PrivatePCH.h"

class FMdpSamplePlugin : public IMdpSamplePlugin
{
	virtual void StartupModule() override
	{
	}

	virtual void ShutdownModule() override
	{
	}
};

IMPLEMENT_MODULE( FMdpSamplePlugin, MdpSamplePlugin )
