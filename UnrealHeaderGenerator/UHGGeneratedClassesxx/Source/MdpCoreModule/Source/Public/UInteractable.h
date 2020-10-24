
#pragma once

// unreal headers
#include "CoreMinimal.h"

// generated headers
#include "UInteractable.generated.h"

UCLASS()
class UInteractable : public UObject {
	GENERATED_CLASS()	
public:

	UFUNCTION()
	void Interact(CHI::Interaction::IInteractor interactor, CHI::Common::IContext context);

	UFUNCTION()
	void OnInteraction(CHI::Common::Event<CHI::Common::IContext> delegate);

	UFUNCTION(Blueprintable, BlueprintNativeEvent, Category = "testvaluecategory")
	FOperation MakeOperation();

};

// using CHI::Interaction::U = UInteractable;
