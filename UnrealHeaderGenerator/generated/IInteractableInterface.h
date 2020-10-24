
#pragma once

// unreal headers
#include "CoreMinimal.h"

// generated headers
#include "IInteractableInterface.generated.h"

UINTERFACE(Blueprintable)
class UNKNOWN_API UInteractableInterface : public UInterface {
	GENERATED_UINTERFACE_BODY()
};

class IInteractableInterface {
	GENERATED_IINTERFACE_BODY()	
public:
	UFUNCTION()
	void Interact(CHI::Interaction::IInteractor interactor, CHI::Common::IContext context);
	UFUNCTION()
	void OnInteraction(CHI::Common::Event<CHI::Common::IContext> delegate);
	UFUNCTION(Blueprintable, BlueprintNativeEvent, Category = "testvaluecategory")
	FOperation MakeOperation();
};

// using CHI::Interaction::IInteractable = IInteractableInterface;
