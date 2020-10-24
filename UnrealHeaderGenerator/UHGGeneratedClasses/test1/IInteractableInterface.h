
#pragma once

// unreal headers
#include "CoreMinimal.h"

// generated headers
#include "IInteractableInterface.generated.h"

UINTERFACE()
class UNKNOWN_API UInteractableInterface : public UInterface {
	GENERATED_UINTERFACE_BODY()
};

class IInteractableInterface {
	GENERATED_IINTERFACE_BODY()	
public:

	UFUNCTION()
	void Interact(CHI::Interaction::Interactor interactor, CHI::Common::Context context);

	UFUNCTION()
	void OnInteraction(CHI::Common::Event<CHI::Common::Context> delegate);

};

// using CHI::Interaction::IInteractable = IInteractableInterface;
