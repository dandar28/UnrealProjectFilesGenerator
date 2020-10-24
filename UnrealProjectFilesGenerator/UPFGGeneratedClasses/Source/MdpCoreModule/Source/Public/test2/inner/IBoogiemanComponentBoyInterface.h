
#pragma once

// unreal headers
#include "CoreMinimal.h"

// generated headers
#include "IBoogiemanComponentBoyInterface.generated.h"

UINTERFACE()
class UNKNOWN_API UBoogiemanComponentBoyInterface : public UInterface {
	GENERATED_UINTERFACE_BODY()
};

class IBoogiemanComponentBoyInterface {
	GENERATED_IINTERFACE_BODY()	
public:

	UFUNCTION()
	void Boogie(ITestNameInterface banana);

};

// using CHI::BoogiemanNS::IBoogiemanComponentBoy = IBoogiemanComponentBoyInterface;
