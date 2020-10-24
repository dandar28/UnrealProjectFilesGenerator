
#pragma once

// unreal headers
#include "CoreMinimal.h"

// generated headers
#include "ITestNameInterface.generated.h"

UINTERFACE()
class UNKNOWN_API UTestNameInterface : public UInterface {
	GENERATED_UINTERFACE_BODY()
};

class ITestNameInterface {
	GENERATED_IINTERFACE_BODY()	
public:

	UFUNCTION()
	void Banaboom(IBoogiemanComponentBoyInterface apple);

};

// using CHI::TestNS::ITestName = ITestNameInterface;
