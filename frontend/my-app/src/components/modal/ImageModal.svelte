<script>
    import Icon from '@iconify/svelte';
    import ImageCarousel from '../ImageCarousel.svelte';
  </script>
  
  <div
    class="pointer-events-auto relative flex w-full flex-col rounded-md border-none bg-white bg-clip-padding text-current shadow-2xl outline-none"
  >
    <div
      class="bg-white overflow-hidden shadow rounded-lg transform transition duration-500 hover:scale-105 hover:-translate-y-1 hover:shadow-xl"
    >
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-gray-300 rounded-md p-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
              <path
                fill="#990f02"
                d="M17 13V7h2v6h-2m0 4v-2h2v2h-2m-4-4V5c0-1.7-1.3-3-3-3S7 3.3 7 5v8c-2.2 1.7-2.7 4.8-1 7s4.8 2.7 7 1s2.7-4.8 1-7c-.3-.4-.6-.7-1-1m-3-9c.6 0 1 .4 1 1v3H9V5c0-.6.4-1 1-1Z"
              />
            </svg>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dt class="text-sm font-medium text-gray-500 truncate font-mono">Temperature</dt>
            <dd class="flex items-baseline">
              <div class="text-lg font-medium text-gray-900 font-mono">28.3˚C</div>
              <div class="ml-2 flex items-baseline text-sm font-mono font-semibold text-red-500">
                <svg
                  class="self-center flex-shrink-0 h-5 w-5 text-indigo-500"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path fill-rule="evenodd" d="M16.707 5" />
                </svg>
                <span class="sr-only"> Remained stable </span>
                +0.0˚C
              </div>
            </dd>
          </div>
  
          <button
            type="button"
            class="box-content rounded-none border-none hover:no-underline hover:opacity-75 focus:opacity-100 focus:shadow-none focus:outline-none"
            data-te-modal-dismiss
            aria-label="Close"
          >
            <Icon icon="radix-icons:cross-1" width="24" />
          </button>
        </div>
        <div class="flex flex-col relative w-full h-[400px]">
          <ImageCarousel />
        </div>
      </div>
    </div>
  </div>
  