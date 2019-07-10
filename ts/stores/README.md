## Custom Store Implementation using RxJS
### Based on NgRX
---

This is a document that outlines how to create a store that acts/works just like NgRX. The only dependency is the RxJS library, the rest is custom code.

* [Actions](#actions)
* [Reducer](#reducer)
* [Store](#store)
* [Usage](#usage)


Creating a store is simply just 3 files in one folder/directory:

Example:
```
|-- app-store
    |-- app.actions.ts
    |-- app.reducer.ts
    |-- app.store.ts
```

## Actions

The actions file should have three things:
* Action types enum
* Action classes
* Action union type

In TypeScript, enums start with a key of 0 by default.
This will coerce to a falsey when use in a if statement 
and throw a compile error when used in a switch/case.
Therefore it is recommended/preferred to start the enumerator at 1.

An action is just a class with a pre-defined type,
which should be one of the types from the enum.
Each action can have its custom constructor for accepting data a.k.a payload.

After defining all of the types, create a type that joins all of them.

Here is an example of an actions file:
```typescript
export enum AppActionTypes {
  LOGIN = 1,
  LOGOUT,
}

export class LoginAction {
  readonly type = AppActionTypes.LOGIN;
  constructor(
    public payload: {
      id: number,
      name: string
    }
  ) {}
}

export class LogoutAction {
  readonly type = AppActionTypes.LOGOUT;
  constructor() {}
}

export type AppActionsUnion = 
  LoginAction |
  LogoutAction;
```


## Reducer

The reducer is a pure function that accepts the state of the store and an action which specifies what occurred. Based on the action's type, the reducer will make the appropriate changes and return the new state. The state argument should match the store's state interface and the action argument should be the union type from the actions file.

To identify what to do, the pure function uses a switch/case on the action's type. In each case, logic can be written on how to change the state; that is up to the developer to decide. Since the action is the union type, each case will have to cast the action as the appropriate type to avoid compile error. This is fine since it will ensure that things works as expected.

Example of a reducer file:
```typescript
import {
  AppActionTypes,
  AppActionsUnion,
  // classes/actions
  LoginAction,
  LogoutAction,
} from './mwc.actions';

import { IAppStateInterface } from './app.store';

export function AppReducer(
  state: IAppStateInterface, 
  action: AppActionsUnion
): IAppStateInterface {
  // any mutations should be done on a new instance.
  // clone the previous state to a new object
  // and work off of that.
  const newState = { ...state };

  // switch/case to handle all of the type of actions.
  switch (action.type) {
    case AppActionTypes.LOGIN: {
      newState.isLoggedIn = true;
      newState.user = {
        ...(<LoginAction>action).payload
      };
      break;
    }
    case AppActionTypes.LOGOUT: {
      newState.isLoggedIn = false;
      newState.user = null;
      break;
    }
  };

  return newState;
}
```


## Store

The store is simply a class that brings the actions and reducer together to manage the state. All properties are private to prevent access from the outside. The store must define an initial value and an interface for the state. The store must also define the logic of how to dispatch actions and share the state to other parts of the code that wants it; this is where RxJS comes in.

The class has the following:

@properties
* `state`: this is the state of the store. It can be any data type or structure. if it is not a primitive, it is recommended to define a type/interface for it.
* `reducer`: this is the pure function that will handle changing the state. every store should have its own custom reducer. the reducer is basically a switch/case tree that defines what action was passed to it and how to mutate the state, using any data if given.
* `eventSubject`: this is the RxJS Subject that will allow other parts of the codebase to listen/subscribe to changes to the state.


@methods
* `dispatch`: this method accepts an action that much match a particular type.
* `getState`: this method will simply return a copy of the state. this is to prevent the state from being mutated from the outside.
* `subscribe`: this method will return a new subscription to the event subject.

Example of a store file:
```typescript
import { AppActionsUnion } from './mwc.actions';
import { AppReducer } from './mwc.reducer';
import { Subject, Subscription } from 'rxjs';

export interface IAppStateInterface {
  isLoggedIn: boolean;
  user: {
    name: string,
    id: number,
  };
}

const initialState: IAppStateInterface = {
  isLoggedIn: false,
  user: null,
};

export class AppStore {
  private state = initialState;
  private reducer = AppReducer;
  private eventSubject: Subject<IAppStateInterface>;

  constructor() {
    this.eventSubject = new Subject<IAppStateInterface>();
  }

  dispatch(action: AppActionsUnion) {
    // get the new state via the reducer.
    const newState = this.reducer(this.state, action);
    // update the state of the store
    this.state = newState;
    // emit a new event to all subscribers with the new state
    this.eventSubject.next(newState);
  }

  getState() {
    // since the state of this store is of type `Object`
    // this is how we get a clone/copy of it
    return {  ...this.state };
  }

  subscribe(callBack: (state) => void): Subscription {
    // this is how the store will allow others to listen to changed to the store
    return this.eventSubject.subscribe(callBack, error => {
      throw error;
    });
  }
}
```

## Usage

Once everything is define, just create a new instance of the store class:
```typescript
const appStore = new AppStore();
```

To get the state:
```typescript
appStore.getState();
```

To subscribe to changes to the state:
```typescript
appStore.subscribe((state) => {
  console.log(state);
});
```

To dispatch an action:
```typescript
const action = new LoginAction({ 
  id: 1, 
  name: 'Test',
});

appStore.dispatch(action);
```

Many store can be created with this approach. When that happens, it may be helpful to consolidate all of the stores into one place:
```typescript
/* 
  all-stores.ts 
*/
import { AppStore } from './app-store/app.store';

// this is just a class that brings all stores together into 1 place
export class Stores {
  appStore: AppStore = new AppStore();
}
```

Then you can do this, which avoids more imports:
```typescript
Stores.appStore.subscribe((state) => {
  console.log(state);
});
```

### AngularJS

In Angular, there is NgRX. However, AngularJS does not have a library for state-management. This is simply an idea for that problem.

In your AngularJS app, simply register the `Stores` class as a service to the module:
```typescript
angular.module('yourApp', [])
  .service('Stores', Stores);
```

Now every part of your application can access the stores.

Example:
```typescript
export const LoginComponent: IComponentOptions = {
  template: './login.component.html',
  bindings: {},
  controller: class implements IOnInit, IOnDestroy {
    static $inject = [
      '$http',
      'Stores',
    ];

    appStoreSubscription: Subscription;

    constructor(
      private $http,
      private stores: Stores,
    ) {}

    $onInit() {
      this.appStoreSubscription = this.stores.appStore.subscribe((state) => {
        console.log(state);
      });
    }

    $onDestroy() {
      if(this.appStoreSubscription) {
        this.appStoreSubscription.unsuscribe();
      }
    }

    loginAction() {
      this.$http.put('/login', dataObj).then(response => {
        const action = new LoginAction(response.user);

        appStore.dispatch(action);
      });
    }
  }
};

angular.module('yourApp', [])
  .component('loginComponent', LoginComponent);
```

Enjoy!

Ryan M. Waite